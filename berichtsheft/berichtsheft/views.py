from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .generate_logbook_pdf import generate_logbook_pdf
from .models import Logbook


def logbook_pdf_view(request, pk):
    logbook = get_object_or_404(
        Logbook.objects.prefetch_related("years__weeks__entries"), pk=pk
    )
    pdf_bytes = generate_logbook_pdf(logbook)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    filename = f"Berichtsheft_{logbook.student_name.replace(' ', '_')}.pdf"
    response["Content-Disposition"] = f'inline; filename="{filename}"'
    return response
