from sqlalchemy.orm import Session
from ..models import models
from ..schemas.schemas import ProductCreate

from uuid import UUID

class ProductRepository:
    def __init__(self, db: Session, shop_id: UUID):
        self.db = db
        self.shop_id = shop_id

    def get_all(self):
        return self.db.query(models.Product).filter(models.Product.shop_id == self.shop_id).all()

    def get_by_barcode(self, barcode: str):
        return self.db.query(models.Product).filter(
            models.Product.barcode == barcode, 
            models.Product.shop_id == self.shop_id
        ).first()

    def create(self, product_in: ProductCreate):
        # Convert Pydantic model to dict, then add shop_id
        product_data = product_in.dict()
        db_product = models.Product(**product_data, shop_id=self.shop_id)
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
    def get_by_id(self, product_id: UUID):
        return self.db.query(models.Product).filter(models.Product.id == product_id, models.Product.shop_id == self.shop_id).first()

    def update(self, product_id: UUID, updates: dict):
        db_product = self.get_by_id(product_id)
        if db_product:
            for key, value in updates.items():
                if key in ['id', 'shop_id']: continue
                if hasattr(db_product, key):
                    setattr(db_product, key, value)
            self.db.commit()
            self.db.refresh(db_product)
        return db_product

    def delete(self, product_id: UUID):
        db_product = self.get_by_id(product_id)
        if db_product:
            self.db.delete(db_product)
            self.db.commit()
            return True
        return False

    def adjust_stock(self, product_id: UUID, quantity: float, type: str, note: str):
        db_product = self.get_by_id(product_id)
        if not db_product: return None
        
        db_product.current_stock += quantity
        
        log = models.StockLog(
            shop_id=self.shop_id,
            product_id=product_id,
            type=type,
            quantity=abs(quantity), # store absolute quantity
            note=note
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def get_logs(self):
        results =  self.db.query(
            models.StockLog,
            models.Product.name.label("product_name")
        ).join(models.Product).filter(
            models.StockLog.shop_id == self.shop_id
        ).order_by(models.StockLog.created_at.desc()).limit(50).all()
        
        # Flatten the result for the API
        return [
            {
                "id": r.StockLog.id,
                "product_id": r.StockLog.product_id,
                "product_name": r.product_name,
                "type": r.StockLog.type,
                "quantity": r.StockLog.quantity,
                "note": r.StockLog.note,
                "created_at": r.StockLog.created_at
            } for r in results
        ]
