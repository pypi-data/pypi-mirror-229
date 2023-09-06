import logging
from os import getenv as env
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, RedirectResponse
from starlette.routing import Route
from starlette.schemas import SchemaGenerator
from starlette.templating import Jinja2Templates
from tortoise.contrib.starlette import register_tortoise
from tortoise_api_model import Model

from tortoise_api.util import jsonify, delete, parse_qs

schemas = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "Example API", "version": "1.0"}}
)

def openapi_schema(request: Request):
    return schemas.OpenAPIResponse(request=request)


class Api:
    app: Starlette
    models: {str: Model}

    def __init__(
        self,
        debug: bool = False,
        # auth_provider: AuthProvider = None, # todo: add auth
    ):
        """
        Parameters:
            debug: Debug SQL queries, api requests
            # auth_provider: Authentication Provider
        """
        self.templates = Jinja2Templates("templates")
        self.routes: [Route] = [
            Route('/{model}/{oid}', self.one_update, methods=['GET', 'POST', 'DELETE']),
            Route('/favicon.ico', lambda req: Response(), methods=['GET']),  # avoid chrome auto favicon load
            Route("/schema", endpoint=openapi_schema, include_in_schema=False),
            Route('/{model}', self.all_create, methods=['GET', 'POST']),
            Route('/', self.api_menu, methods=['GET']),
        ]
        self.debug = debug

    def start(self, models_module):
        self.models: {str: type[Model]} = {key: model for key in dir(models_module) if isinstance(model := getattr(models_module, key), type(Model)) and model.mro()[1]==Model}
        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
        self.app = Starlette(debug=self.debug, routes=self.routes)
        load_dotenv()
        register_tortoise(self.app, db_url=env("DB_URL"), modules={"models": [models_module]}, generate_schemas=self.debug)
        return self.app

    # ROUTES
    async def api_menu(self, _: Request):
        return JSONResponse(list(self.models))

    async def all_create(self, request: Request):
        model: type[Model] = self._get_model(request)
        if request.method == 'POST':
            data = parse_qs(await request.body())
            obj: Model = await model.upsert(data)
            return RedirectResponse('/list/'+model.__name__, 303) # create # {True: 201, False: 202}[res[1]]
        objects: [Model] = await model.all().prefetch_related(*model._meta.fetch_fields)
        data = [await jsonify(obj) for obj in objects]
        return JSONResponse({'data': data}) # show all

    async def one_update(self, request: Request):
        model: type[Model] = self._get_model(request)
        oid = request.path_params['oid']
        if request.method == 'POST':
            data = parse_qs(await request.body())
            res = await model.upsert(data, oid)
            # return JSONResponse(await jsonify(res[0]), status_code=202) # update
            return RedirectResponse('/list/'+model.__name__, 303) # create # {True: 201, False: 202}[res[1]]
        elif request.method == 'DELETE':
            await delete(model, oid)
            return JSONResponse({}, status_code=202) # delete
        obj = await model.get(id=oid).prefetch_related(*model._meta.fetch_fields)
        return JSONResponse(await jsonify(obj)) # show one


    # UTILS
    def _get_model(self, request: Request) -> type[Model]:
        model_id: str = request.path_params['model']
        return self.models.get(model_id)
