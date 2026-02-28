"""
API views for MNIST Digit Recognition.
"""
import base64
import io
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Prediction, TrainingRun, PredictionProbability


def _get_predictor():
    """Get predictor with Django MODEL_PATH."""
    from predictor import get_predictor
    return get_predictor(model_path=settings.MODEL_PATH)


@api_view(['GET'])
def api_root(request):
    """API info and health."""
    return Response({
        'name': 'MNIST Digit Recognition API',
        'status': 'running',
        'version': '3.0.0',
        'endpoints': {
            'predict': 'POST /api/predict | POST /api/predict/base64',
            'train': 'POST /api/train',
            'status': 'GET /api/model/status',
            'samples': 'GET /api/samples',
            'evaluate': 'GET /api/evaluate',
            'predictions': 'GET /api/predictions',
            'training_runs': 'GET /api/training-runs',
        },
    })


@api_view(['GET'])
def health(request):
    """Health check."""
    predictor = _get_predictor()
    loaded = predictor.load()
    return Response({'status': 'ok', 'model_loaded': loaded})


@api_view(['GET'])
def model_status(request):
    """Model loaded status."""
    predictor = _get_predictor()
    loaded = predictor.load()
    return Response({'loaded': loaded, 'path': settings.MODEL_PATH})


@api_view(['POST'])
def predict_file(request: Request):
    """Predict from uploaded image file. Stores result in DB."""
    parser_classes = [MultiPartParser]
    if 'file' not in request.FILES:
        return Response({'detail': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    file = request.FILES['file']
    if not file.content_type or not file.content_type.startswith('image/'):
        return Response({'detail': 'File must be an image'}, status=status.HTTP_400_BAD_REQUEST)

    predictor = _get_predictor()
    if not predictor.load():
        return Response({'detail': 'Model not loaded. Train via POST /api/train'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        result = predictor.predict(file.read())
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Store in DB
    pred_obj = Prediction.objects.create(
        digit=result.digit,
        confidence=result.confidence,
        source='file',
    )
    for i, p in enumerate(result.probabilities):
        PredictionProbability.objects.create(
            prediction=pred_obj,
            digit_class=i,
            probability=p,
        )

    return Response({
        'digit': result.digit,
        'confidence': result.confidence,
        'probabilities': result.probabilities,
        'label': result.label,
        'id': pred_obj.id,
    })


@api_view(['POST'])
def predict_base64(request: Request):
    """Predict from base64 image (e.g. canvas.toDataURL). Stores result in DB."""
    image_b64 = request.data.get('image')
    if not image_b64:
        return Response({'detail': 'Missing image field'}, status=status.HTTP_400_BAD_REQUEST)

    predictor = _get_predictor()
    if not predictor.load():
        return Response({'detail': 'Model not loaded. Train via POST /api/train'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        result = predictor.predict(image_b64)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Store in DB
    pred_obj = Prediction.objects.create(
        digit=result.digit,
        confidence=result.confidence,
        source='canvas',
    )
    for i, p in enumerate(result.probabilities):
        PredictionProbability.objects.create(
            prediction=pred_obj,
            digit_class=i,
            probability=p,
        )

    return Response({
        'digit': result.digit,
        'confidence': result.confidence,
        'probabilities': result.probabilities,
        'label': result.label,
        'id': pred_obj.id,
    })


@api_view(['POST'])
def train(request: Request):
    """Train a new model. Saves run to DB."""
    model_type = request.data.get('model_type', 'advanced')
    epochs = int(request.data.get('epochs', 15))
    batch_size = int(request.data.get('batch_size', 128))

    from model import load_mnist_data, build_cnn_model, build_simple_model, train_model

    predictor = _get_predictor()
    (x_train, y_train), (x_test, y_test) = load_mnist_data()

    if model_type.lower() == 'simple':
        model = build_simple_model()
    else:
        model = build_cnn_model()

    history, test_loss, test_acc = train_model(
        model, x_train, y_train, x_test, y_test,
        epochs=epochs,
        batch_size=batch_size,
    )

    model.save(settings.MODEL_PATH)
    predictor.set_model(model)

    # Store in DB
    TrainingRun.objects.create(
        model_type=model_type.lower(),
        epochs=epochs,
        batch_size=batch_size,
        test_accuracy=float(test_acc),
        test_loss=float(test_loss),
    )

    return Response({
        'message': 'Training complete',
        'test_accuracy': float(test_acc),
        'test_loss': float(test_loss),
    })


@api_view(['GET'])
def samples(request):
    """Get MNIST samples as base64 for gallery."""
    import numpy as np
    from PIL import Image
    from model import load_mnist_data

    count = int(request.query_params.get('count', 10))
    digit = request.query_params.get('digit')
    if digit is not None:
        digit = int(digit)

    (x_train, y_train), _ = load_mnist_data()
    y_labels = np.argmax(y_train, axis=1)

    if digit is not None:
        indices = np.where(y_labels == digit)[0]
    else:
        indices = np.arange(len(x_train))

    indices = np.random.choice(indices, min(count, len(indices)), replace=False)
    samples_list = []
    for idx in indices:
        img = (x_train[idx].squeeze() * 255).astype('uint8')
        pil = Image.fromarray(img, mode='L')
        buf = io.BytesIO()
        pil.save(buf, format='PNG')
        samples_list.append({
            'image_base64': base64.b64encode(buf.getvalue()).decode(),
            'label': int(y_labels[idx]),
        })

    return Response({'samples': samples_list})


@api_view(['GET'])
def evaluate(request):
    """Model evaluation metrics."""
    from sklearn.metrics import confusion_matrix, classification_report

    predictor = _get_predictor()
    if not predictor.load():
        return Response({'detail': 'Model not loaded'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    from model import load_mnist_data
    _, (x_test, y_test) = load_mnist_data()
    model = predictor._model
    y_pred = model.predict(x_test, verbose=0).argmax(axis=1)
    y_true = y_test.argmax(axis=1)

    return Response({
        'accuracy': float((y_pred == y_true).mean()),
        'confusion_matrix': confusion_matrix(y_true, y_pred).tolist(),
        'classification_report': classification_report(y_true, y_pred, output_dict=True),
    })


@api_view(['GET'])
def prediction_list(request):
    """List stored predictions from DB (paginated)."""
    from .serializers import PredictionSerializer

    predictions = Prediction.objects.all()[:100]
    serializer = PredictionSerializer(predictions, many=True)
    return Response({
        'count': Prediction.objects.count(),
        'results': serializer.data,
    })


@api_view(['GET'])
def training_run_list(request):
    """List stored training runs from DB."""
    from .serializers import TrainingRunSerializer

    runs = TrainingRun.objects.all()[:50]
    serializer = TrainingRunSerializer(runs, many=True)
    return Response({'results': serializer.data})
