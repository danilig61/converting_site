import json
import zipfile
import io
import os
import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

class ConvertZipFilesAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'Файл не загружен'}, status=400)

        file = request.FILES['file']
        zip_data = io.BytesIO(file.read())

        converted_files = self.convert_files_to_json(zip_data)

        # Создание новой папки для сохранения преобразованных файлов
        output_folder = os.path.join(os.getcwd(), 'converted_files')
        os.makedirs(output_folder, exist_ok=True)

        # Сохранение каждого файла в формате JSON в новой папке
        for filename, cookies in converted_files.items():
            sanitized_filename = filename.replace('/', '_')
            output_file_path = os.path.join(output_folder, f"{os.path.splitext(sanitized_filename)[0]}.json")
            with open(output_file_path, 'w') as output_file:
                json.dump(cookies, output_file, indent=2, ensure_ascii=False)

        return Response({'message': 'Файлы успешно преобразованы и сохранены'})

    def convert_files_to_json(self, zip_data):
        converted_files = {}
        with zipfile.ZipFile(zip_data, 'r') as zip_ref:
            for filename in zip_ref.namelist():
                with zip_ref.open(filename) as file:
                    file_content = file.read()
                    decoded_content = file_content.decode('utf-8')
                    cookies = self.parse_cookies(decoded_content)
                    converted_files[filename] = cookies
        return converted_files

    def parse_cookies(self, content):
        cookies = []
        lines = content.split('\n')
        for line in lines:
            if line.strip() != '':
                x = line.strip().split('\t')
                if len(x) >= 7:
                    key = {}
                    key['domain'] = x[0]
                    key['httpOnly'] = x[1] == "TRUE"
                    key['path'] = x[2]
                    key['secure'] = x[3] == "TRUE"
                    key['expirationDate'] = int(x[4])
                    key['name'] = x[5]
                    key['value'] = x[6]
                    cookies.append(key)
        return cookies
