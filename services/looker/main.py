import unittest
import click
from datetime import datetime

from flask.cli import FlaskGroup
from project import create_app, db, config
from project.api.dx_looker_service import build_service
from project.api.json_cleaner import JsonCleaner, read_json
from project.api.looker_api_handler import LookerApiHandler, build_handler
from project.api.models import InvoicingByLibrary, SendsByLibrary


app = create_app()
cli = FlaskGroup(create_app=create_app)
handler = build_handler()
conf = config.DevelopmentConfig
json_cleaner = JsonCleaner(read_json(conf.TRANSFORMATIONS))
services = {
    "4404": build_service("4404", db, handler, SendsByLibrary, json_cleaner),
    "4405": build_service("4405", db, handler, InvoicingByLibrary, json_cleaner),
}


@cli.command()
@click.option("-l")
def recreate_db(l):
    services[l].db.drop_all()
    services[l].db.create_all()
    services[l].db.session.commit()


@cli.command()
def test():
    """ Runs the tests without code coverage"""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@cli.command()
@click.option("-l")
def pull_looks(l: str):
    service = services.get(l, None)
    if service is None:
        print("{} is not a legal look id".format(l))
    else:
        services[l].cache_look()
        print(service.db_cache.db_model.query.all())


if __name__ == "__main__":

    # conf = config.DevelopmentConfig
    # c_id, c_secret, endpoint = get_looker_credentials()
    # handler = LookerApiHandler(endpoint)
    # handler.login(c_id, c_secret)
    # json_cleaner = JsonCleaner(read_json(conf.TRANSFORMATIONS))
    # services = build_services(conf.LOOKS, db, handler, json_cleaner)
    # for s_id, service in services.items():
    #     service.cache_look()
    cli()
