from google import genai

# Dán API Key của bạn vào đây
API_KEY = "" 
client = genai.Client(api_key=API_KEY)

print("--- DANH SÁCH CÁC MODEL BẠN ĐƯỢC PHÉP DÙNG ---")
for model in client.models.list():
    print(model.name)