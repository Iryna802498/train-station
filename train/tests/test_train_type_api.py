import os
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from train.models import TrainType
from train.serializers import TrainTypeSerializer


TRAIN_TYPE_URL = reverse("train:train-type-list")


def sample_train_type(**params):
    defaults = {"name": "Intercity"}
    defaults.update(params)
    return TrainType.objects.get_or_create(
        name=defaults["name"],
        defaults=defaults
    )[0]


def detail_url(train_type_id):
    return reverse("train:train-type-detail", args=[train_type_id])


def sample_image_file(size=(100, 100)):
    """Return a simple uploaded image file"""
    file = BytesIO()
    image = Image.new("RGB", size)
    image.save(file, "JPEG")
    file.seek(0)
    return SimpleUploadedFile("test.jpg", file.read(), content_type="image/jpeg")


def image_upload_url(train_type_id):
    """Return URL for recipe image upload"""
    return reverse("train:train-type-upload-image", args=[train_type_id])


def upload_test_image(client, url, size=(10, 10)):
    """Upload a test image via client to the given URL"""
    file = BytesIO()
    image = Image.new("RGB", size)
    image.save(file, "JPEG")
    file.seek(0)
    return client.post(
        url,
        {
            "image": SimpleUploadedFile(
                "upload.jpg",
                file.read(),
                content_type="image/jpeg"
            )
        },
        format="multipart"
    )


class UnauthenticatedTrainTypeApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required_train_type(self):
        res = self.client.get(TRAIN_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainTypeApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.user",
            "userpass"
        )
        self.client.force_authenticate(self.user)
        self.train_type = sample_train_type()

    def test_train_type_list(self):
        self.train_type
        res = self.client.get(TRAIN_TYPE_URL)
        train_types = TrainType.objects.order_by("id")
        serializer = TrainTypeSerializer(train_types, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_train_type_detail(self):
        train_type = sample_train_type(
            name="Intercity",
            image=sample_image_file()
        )
        url = detail_url(train_type.id)
        res = self.client.get(url)
        serializer = TrainTypeSerializer(train_type)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AdminTrainTypeApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_superuser(
            "admin@admin.com",
            "adminpass"
        )
        self.client.force_authenticate(self.admin)
        self.train_type = sample_train_type()

    def tearDown(self):
        if self.train_type.image:
            self.train_type.image.delete()

    def test_create_train_type(self):
        payload = {
            "name": "Intercity+",
            "image": ""
        }
        res = self.client.post(TRAIN_TYPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], payload["name"])
        

    def test_upload_image_to_train_type(self):
        url = image_upload_url(self.train_type.id)
        res = upload_test_image(self.client, url)
        self.train_type.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.train_type.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.train_type.id)
        res = self.client.post(url, {"image": "not-an-image"}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_image_url_is_shown_in_detail(self):
        url = image_upload_url(self.train_type.id)
        res = upload_test_image(self.client, url)
        self.train_type.refresh_from_db()
        self.assertIn("image", res.data)


    def test_image_url_is_shown_in_list(self):
        url = image_upload_url(self.train_type.id)
        res = upload_test_image(self.client, url)
        self.train_type.refresh_from_db()
        self.assertIn("image", res.data)


    def test_put_not_allowed(self):
        url = detail_url(self.train_type.id)
        payload = {"name": "Updated"}
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_delete_not_allowed(self):
        url = detail_url(self.train_type.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
