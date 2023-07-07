from passlib.context import CryptContext
import io
import csv

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def to_camel(snake_str):
    parts = snake_str.split('_')
    return parts[0] + ''.join(w.title() for w in parts[1:])


def convert_to_list(*args, unique=False) -> list:
    lst = []
    for arg in args:
        if isinstance(arg, str):
            lst.append(arg)
        else:
            try:
                lst.extend(arg)
            except TypeError:
                pass

    if unique:
        lst = list(set(lst))

    return lst


def query_result_to_csv(header, query_result):
    file = io.StringIO()
    writer = csv.writer(file, delimiter=",")
    writer.writerow(header)

    for obj in query_result:
        writer.writerow([getattr(obj, attr) for attr in header])

    return file


def query_result_to_file(header, query_result):
    with open("backend/temp_file.csv", "w") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(header)

        for obj in query_result:
            writer.writerow([getattr(obj, attr) for attr in header])
