from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Item(BaseModel):
    name: str
  

class ResponseModel(BaseModel):
    items: List[Item]
    count: int
    

# @app.get("/coolies/", response_model=ResponseModel)
# def functionName23():
#     items = [Student(name="Vinay", id=12)]
#     return {"Student": Student, "count": len(Student)}

@app.get("/items/", response_model=ResponseModel)
def get_items():
    items = [Item(name="item1", price=10.0), 
             Item(name="item2", price=20.0),
             Item(name="item3", price=34.0)]
    return {"items": items, "count": len(items)}

@app.get("/getZero",response_model=ResponseModel)
def functionName():
     items = [Item(name="item1", price=10.0), 
             Item(name="item2", price=20.0),
             ]
     return {"items": items, "count": len(items)}



from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Items API (homework)")

# Pydantic models
class ItemBase(BaseModel):
    name: str = Field(..., example="Notebook")
    price: float = Field(..., ge=0, example=9.99)
    description: Optional[str] = Field(None, example="A ruled notebook")

class ItemCreate(ItemBase):
    # used for incoming POST (could be same as ItemBase)
    pass

class ItemUpdate(BaseModel):
    # allow partial updates
    name: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None

class ItemResponse(ItemBase):
    id: int

# In-memory storage
items: Dict[int, ItemResponse] = {}
_next_id = 1

def _get_next_id() -> int:
    global _next_id
    nid = _next_id
    _next_id += 1
    return nid

# READ all
@app.get("/items", response_model=Dict[int, ItemResponse])
def read_items():
    """Return all items (response_model ensures correct shape)."""
    return items

# READ one
@app.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int):
    item = items.get(item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item

# CREATE (POST)
@app.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_in: ItemCreate):
    """Create a new item. response_model returns an ItemResponse with id."""
    item_id = _get_next_id()
    item = ItemResponse(id=item_id, **item_in.dict())
    items[item_id] = item
    return item

# UPDATE (PUT) - full replace
@app.put("/items/{item_id}", response_model=ItemResponse)
def replace_item(item_id: int, item_in: ItemCreate):
    """
    Replace an existing item with the provided data.
    Use PUT for full replacement; returns the updated item.
    """
    if item_id not in items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    updated = ItemResponse(id=item_id, **item_in.dict())
    items[item_id] = updated
    return updated

# PATCH-like (partial update) using ItemUpdate
@app.patch("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_in: ItemUpdate):
    """
    Partial update (PATCH semantics) — only fields provided will change.
    Useful when you don't want to send the whole resource.
    """
    stored = items.get(item_id)
    if not stored:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    updated_data = stored.dict()
    update_fields = item_in.dict(exclude_unset=True)
    updated_data.update(update_fields)
    updated = ItemResponse(**updated_data)
    items[item_id] = updated
    return updated

# DELETE
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    del items[item_id]
    return None
