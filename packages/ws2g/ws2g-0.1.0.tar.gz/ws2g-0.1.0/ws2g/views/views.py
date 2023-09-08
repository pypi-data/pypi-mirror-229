path_view = {}


def route(identifier, path=None):
    if not path:
        path = identifier

    def wrapper(view_class):
        # Route path to an instance of the class
        # [1:] - without leading '/'
        file_path = path[1:]
        file_path = "content/" + file_path
        if file_path == "content/":
            file_path = "content/index.html"

        path_view[identifier] = view_class(file_path)
        return view_class

    return wrapper


def render(page):
    return path_view[page].build_GET_response()


class BaseView:
    def __init__(self, file_path="", status_code=404, content_type="text/html") -> None:
        self.file_path = file_path
        self.status_code = status_code
        self.headers = {
            "Content-type": content_type,
        }

    def build_GET_response(self) -> str:
        return "Not implemented"

    def build_POST_response(self) -> str:
        return "Not implemented"

    def __str__(self) -> str:
        return (
            "File path: "
            + self.file_path
            + "; status="
            + str(self.status_code)
            + "; headers="
            + str(self.headers)
        )


class CSS(BaseView):
    def __init__(self, file_path, status_code=200, content_type="text/css") -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path) as f:
            return f.read()


class JavaScript(BaseView):
    def __init__(
        self, file_path="", status_code=200, content_type="text/javascript"
    ) -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path) as f:
            return f.read()


class PHP(BaseView):
    def __init__(self, file_path="", status_code=200, content_type="text/html") -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path) as f:
            return f.read()


class Image(BaseView):
    def __init__(self, file_path, status_code=200, content_type="image/jpeg") -> None:
        super().__init__(file_path, status_code, content_type)

    def build_GET_response(self) -> str:
        with open(self.file_path, "rb") as f:
            return f.read()


def prepare_special_routes():
    import glob
    import os

    # There are probably more cases that should be handled
    image_extensions = ["gif", "jpg", "png", "tiff"]

    # root_dir needs a trailing slash (i.e. /root/dir/)
    for file_path in glob.iglob("content/" + "**/**", recursive=True):
        file_path = file_path.lower()
        file_path = file_path.replace("\\", "/")

        request_path = file_path[file_path.find("/", 2) :]
        if (
            os.path.isfile(file_path)
            and not file_path.endswith(".html")
            and request_path not in path_view
        ):
            if file_path.endswith(".css"):
                path_view[request_path] = CSS(file_path, status_code=200)
            elif any(file_path.endswith(ext) for ext in image_extensions):
                content_type = file_path[file_path.rfind(".") + 1 :]
                if content_type == "jpg":
                    content_type = "jpeg"

                path_view[request_path] = Image(
                    file_path, content_type="image/" + content_type
                )
            elif file_path.endswith(".svg"):
                path_view[request_path] = Image(
                    file_path, content_type="image/" + "svg+xml"
                )
            elif file_path.endswith(".js"):
                path_view[request_path] = JavaScript(file_path)
            elif file_path.endswith(".php"):
                path_view[request_path] = PHP(file_path)
            else:
                print("Unhandled special route:", file_path)

    # for k, v in path_view.items():
    #     print(k, v)
