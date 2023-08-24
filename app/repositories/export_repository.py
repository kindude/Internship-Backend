import csv

from fastapi.responses import JSONResponse, FileResponse
class ExportRepository:

    def generate_csv_response(self, user_results, filename):
        csv_filename = filename
        csv_response = FileResponse(csv_filename,
                                    headers={"Content-Disposition": f"attachment; filename={csv_filename}"})

        with open(csv_filename, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["user_id", "company_id", "quiz_id", "question", "option", "is_correct", "time"])

            for result in user_results:
                quiz_data = {
                    "user_id": result["user_id"],
                    "company_id": result["company_id"],
                    "quiz_id": result["quiz_id"],
                    "question": result["question"],
                    "option": result["option"],
                    "is_correct": result["is_correct"],
                    "time": result["time"]
                }
                csv_writer.writerow([quiz_data["user_id"], quiz_data["company_id"], quiz_data["quiz_id"],
                                     quiz_data["question"], quiz_data["option"], quiz_data["is_correct"],
                                     quiz_data["time"]])
        return csv_response

