import logging

import boto3
import botocore
import requests
from botocore.client import Config
from django.conf import settings

logger = logging.getLogger(__name__)


class Cloudflare:
    def __init__(self, user=None):
        # Get what user wants access to exam
        self.user = user

        # Env variables to get access to bucket
        self.account_id = settings.CF_ACCOUNT_ID
        self.video_image_token = settings.CF_VIDEO_IMAGE_TOKEN
        self.access_key_id = settings.EXAMS_ACCESS_KEY_ID
        self.secret_access_key = settings.EXAMS_SECRET_ACCESS_KEY
        self.bucket_name = settings.EXAMS_BUCKET_NAME

        # Configure the S3 client for Cloudflare R2
        self.s3_client = self._create_client()

    def _create_client(self):
        environment = settings.ENVIRONMENT
        if environment == "PROD":
            return boto3.client(
                "s3",
                endpoint_url=f"https://{self.account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                config=Config(signature_version="s3v4"),
            )

    def get_document(self, document: str):
        logger.info(f"El usuario '{self.user}' quiere acceder a '{document}'")
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=document
            )
            logger.info(
                f"El usuario '{self.user}' accedió exitosamente a '{document}'"
            )
        except botocore.exceptions.ClientError as error:
            logger.warn(
                f"El usuario '{self.user}' falló al descargar '{document}'"
            )
            raise error

        return response["Body"]

    def put_exam(self, file, name):
        logger.info(f"Se va a subir el examen {name}")
        try:
            self.s3_client.put_object(
                Body=file, Bucket=self.bucket_name, Key=name
            )
            logger.info(f"Se va a subió exitosamente el examen {name}")
        except botocore.exceptions.ClientError as error:
            logger.warn(f"Hubo un error al subir el examen '{name}'")
            raise error

    def get_video_signed_url(self, video_uid):
        # The URL for the API request
        url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/stream/{video_uid}/token"

        # Headers for the request
        headers = {
            "Authorization": f"Bearer {self.video_image_token}",
            "Content-Type": "application/json",
        }

        # Make the POST request
        response = requests.post(url, headers=headers)
        # Print the response
        if response.status_code != 200:
            return {"error": "Error al obtener la URL del video "}
        else:
            return response.json()
