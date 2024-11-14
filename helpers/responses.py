from django.http import StreamingHttpResponse


def get_streaming_response(streaming, filename, type):
    if type == "txt":
        return StreamingHttpResponse(
            streaming,
            content_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.txt"
            },
        )
    elif type == "csv":
        return StreamingHttpResponse(
            streaming,
            content_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.csv"
            },
        )

    elif type == "xlsx":
        response = StreamingHttpResponse(
            streaming,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.xlsx"
            },
        )
        response["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response

    elif type == "pdf":
        response = StreamingHttpResponse(
            streaming,
            content_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}.pdf"
            },
        )
        response["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response
