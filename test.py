import requests
import json
import psycopg2
import os
import tempfile

class PostgresLLMHandler:
    def __init__(self, db_name, user, password, host="localhost", port=5432, openrouter_api_key=None):
    
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.openrouter_api_key = openrouter_api_key
        self.temp_file_path = None  

        try:
            self.conn = psycopg2.connect(
                dbname=db_name,
                user=user,
                password=password,
                host=host,
                port=port
            )
            self.cursor = self.conn.cursor()
            print("Database connection established.")
        except psycopg2.OperationalError as e:
            print(f"Database connection failed: {e}")

    def verify_credentials(self):
        try:
            self.cursor.execute("SELECT 1")  # Simple test query
            return "Credentials are valid."
        except psycopg2.OperationalError as e:
            return f"Credential Verification Failed: {e}"
        except Exception as e:
            return f"Unexpected Error: {e}"

    def query_db(self, query):
    
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            row_count = len(results)

            if row_count == 0:
                return "No data found."
            elif row_count <= 100:
                return results
            else:
                temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt")
                self.temp_file_path = temp_file.name 
                with open(self.temp_file_path, "w") as f:
                    for row in results[100:]:
                        f.write(str(row) + "\n")
                
                return results[:100], f"Remaining {row_count - 100} rows saved to {self.temp_file_path}"
        except Exception as e:
            return f"Error executing query: {e}"

    def read_temp_file(self):
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            with open(self.temp_file_path, "r") as f:
                return f.readlines()
        return "No temporary file found or already deleted."

    def delete_temp_file(self):
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)
            self.temp_file_path = None
            return "Temporary file deleted."
        return "No file found to delete."

    def call_openrouter(self, prompt):
        if not self.openrouter_api_key:
            return "Error: OpenRouter API key is missing."

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}"
        }
        payload = json.dumps({
            "model": "google/gemini-flash-1.5",
            "messages": [{"role": "user", "content": prompt}]
        })

        try:
            response = requests.post(url, headers=headers, data=payload)
            return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response.")
        except Exception as e:
            return f"Error calling OpenRouter: {e}"

    def close_connection(self):
        self.cursor.close()
        self.conn.close()
        print("Database connection closed.")