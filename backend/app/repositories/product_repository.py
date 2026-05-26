from sqlalchemy.orm import Session
from ..models.models import Product
from ..schemas.schemas import ProductCreate

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Product).all()

    def get_by_barcode(self, barcode: str):
        return self.db.query(Product).filter(Product.barcode == barcode).first()

    def create(self, product_in: ProductCreate):
        db_product = Product(**product_in.dict())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
