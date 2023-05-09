import blog.models as models
import blog.schemas as schemas
import uvicorn
from blog.database import engine, SessionLocal
from fastapi import FastAPI, Depends, status, Response, HTTPException
from pathlib import Path
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/blog', status_code=status.HTTP_201_CREATED)
def create(request: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.delete('/blog/{id}', status_code=status.HTTP_204_NO_CONTENT)
def destroy(id, db: Session = Depends(get_db)):
    db.query(models.Blog).filter(models.Blog.id == id).delete(synchronize_session=False)

    db.commit()

    return 'done'


@app.put('/blog/{book_id}', status_code=status.HTTP_202_ACCEPTED)
def update(book_id, request: schemas.Blog, db: Session = Depends(get_db)):
    print(book_id)
    print(request)
    blog: models.Blog = db.query(models.Blog).filter(models.Blog.id == book_id).first()
    if blog is not None:
        blog.title = request.title
        blog.body = request.body
        db.commit()

    return 'updated'


@app.get('/blog')
def all(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs


@app.get('/blog/{id}')
def show(id, response: Response, db: Session = Depends(get_db), status_code=200):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Blog with the id {id} is not available')
    return blog


if __name__ == "__main__":
    uvicorn.run(f"{Path(__file__).stem}:app", host="0.0.0.0", port=8080, log_level="info", reload=True, workers=2)
