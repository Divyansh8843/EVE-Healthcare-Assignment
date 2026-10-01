from app.core.database import SessionLocal
from app.models.diagnostic_centre import DiagnosticCentre
import traceback

print("Trying to insert into database...")
db = SessionLocal()
try:
    centre = DiagnosticCentre(name="Test Centre", location="Test Location")
    db.add(centre)
    db.commit()
    print("Success!")
except Exception as e:
    print("Exception occurred:")
    traceback.print_exc()
finally:
    db.close()
