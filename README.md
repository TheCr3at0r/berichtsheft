# Berichtsheft

I created this project to provide an easy way to generate my weekly **Berichtsheft**. In Germany, apprentices are required to keep a **Berichtsheft**, and your company determines whether it should be updated daily or weekly. This project is designed for the weekly format.

It is a Django application, which may seem a bit overkill, but it offers a simple and user-friendly frontend out of the box. Since it is intended for local use only, it runs in DEBUG mode.

## Before you Start

Setup is straightforward, but there are a few preparatory steps before you can create your report. To save time, my trainer and I signed our documents in advance; this application simply inserts our signatures into the PDF when generating the report.

Please review the following checklist before you begin:

### Checklist

1. Do you want to include a logo (e.g., your company’s logo) in your report? If yes, see **How to Add Your Logo**.
2. Do you want to automatically include signatures? If yes, see **How to Add Your Signatures**.
3. Do you want to use a custom font? If yes, see **How to Add a Custom Font**.

### How to Add Your Logo

Place your logo named **logo.png** in the `berichtsheft/static/images/` directory. The logo is loaded in `berichtsheft/berichtsheft/generate_logbook_pdf.py` at line 270:

```python
logo = Image(logo_path, width=150, height=40)
```

If the logo’s dimensions need adjusting, modify the `width` and `height` parameters on that line.

### How to Add Your Signatures

Place the trainer’s signature as **signature_trainer.png** and your signature as **signature_student.png** in the `berichtsheft/static/images/` directory.

### How to Add a Custom Font

By default, this project uses `Roboto-Regular.ttf` located in `berichtsheft/static/fonts/`. To use a different font, add your `.ttf` file to that directory and update lines 23–24 in `berichtsheft/berichtsheft/generate_logbook_pdf.py`:

```python
font_path = os.path.join(settings.STATIC_ROOT, "fonts", "Roboto-Regular.ttf")
pdfmetrics.registerFont(TTFont("Roboto", font_path))
```

Replace `Roboto-Regular.ttf` in line 23 with the filename of your custom font.

## Setting Up the Application

First, create the `.env` file by copying `.env.example` and filling in the values where indicated.

Once the checklist is complete, build the Docker image:

```bash
docker-compose up -d --build
```

Then create a Django superuser:

```bash
docker-compose exec django python manage.py createsuperuser --username <your_username> --email <your_email>
```

You will be prompted to set a password. After that, open your browser.

## Writing Your Report

### Logbook

Visit `http://localhost:8000/admin` and log in with your superuser credentials. First, add a Logbook:

- **Student name**: Hans Otto
- **Start year**: 2023
- **Student address**: Hans Otto Straße 90, 23422 Unterottohausen
- **Profession**: Fachinformatiker
- **Specialty**: Anwendungsentwicklung
- **Company**: Otto Computers
- **Trainer**: Franz Otto

### Years

In your Logbook, add a Year and set the number to **1**. You can create all years at once, but starting with one year keeps things simpler.

### Weeks

After adding a Year, create Weeks. Apprenticeships usually start on September 1. If September 1 is not a Monday, the first week still starts on September 1 (or on Monday if September 1 falls on a weekend). Enter **1** as the week number for the first week.

### Tasks

Tasks require a type, a name, and the number of hours:

1. **Betriebliche Tätigkeiten** (Operational tasks)
2. **Unterweisungen / Schulungen** (Training)
3. **Berufsschulthemen** (Vocational school topics)

Enter each task’s name and the hours spent. You can add tasks individually in the admin, but it’s easier to manage them in the TASKS section when creating or editing a week.

## Generating Your Report

To view your report as a PDF, go to `http://localhost:8000/logbook/1`, where `1` is your Logbook’s ID. You can then check for errors more easily in the PDF than in the admin interface.
