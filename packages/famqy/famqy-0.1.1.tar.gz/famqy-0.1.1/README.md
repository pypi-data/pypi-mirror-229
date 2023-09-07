# Famqy

FastAPI MongoDB query build


## Usage

```python
import uvicorn
from fastapi import FastAPI, Depends

from famqy import filters, pagination, Operations, SortConfig

app = FastAPI()


@app.get("/")
def home(
    name_filters: dict = Depends(filters("name", "str", [Operations.EQ, Operations.CONTAINS])),
    pag = Depends(pagination({}, {}, SortConfig(values=["name"], config={})))
):
    print(name_filters)
    print(pag.dict())


if __name__ == "__main__":
    uvicorn.run(app)
```