from fastapi import APIRouter,status,Depends
from fastapi.exceptions import HTTPException
from src.books.schemas import UpdateBookModel,BookCreateModel, BookResponseModel, BookDetailModel
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from typing import List
from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.errors import BookNotFound

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin","user"]))


@book_router.get('/',response_model=List[BookResponseModel],dependencies=[role_checker])
async def get_all_books(session: AsyncSession = Depends(get_session)) :
    books = await book_service.get_all_books(session)
    return books


@book_router.get('/user/{user_uid}',response_model=List[BookResponseModel],dependencies=[role_checker])
async def get_user_submission(user_uid: str, session: AsyncSession = Depends(get_session)) :
    books = await book_service.get_user_books(user_uid, session)
    return books

@book_router.post('/',status_code= status.HTTP_201_CREATED,response_model=BookResponseModel,dependencies=[role_checker])
async def create_a_book(book_data: BookCreateModel, session: AsyncSession = Depends(get_session),
 token_details: dict = Depends(access_token_bearer)) -> str :
    user_uid = token_details.get('user')['user_uid']
    new_book = await book_service.create_book(book_data,user_uid, session)
    return new_book

@book_router.get('/{book_uid}',response_model=BookDetailModel,dependencies=[role_checker])
async def get_book(book_uid: str, session: AsyncSession = Depends(get_session),token_details: dict = Depends(access_token_bearer)) :
    book = await book_service.get_book(book_uid, session)
    if book : 
        return book 
    raise BookNotFound()


@book_router.patch('/{book_uid}',dependencies=[role_checker])
async def update_book(book_uid: str,new_book: UpdateBookModel, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)) -> str :
    updated_book = await book_service.update_book(book_uid, new_book, session)
    if updated_book :
        return "book updated sucessfully"
    raise BookNotFound()


@book_router.delete('/{book_uid}',dependencies=[role_checker])
async def delete_book(book_uid: str, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)) -> str :
    book_to_delete = await book_service.delete_book(book_uid, session)
    if book_to_delete :
        return "book deleted sucessfully"
    raise BookNotFound()