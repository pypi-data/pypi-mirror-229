from . import models
from huscy.project_design.models import DataAcquisitionMethod, Experiment, Session


def create_experiment(project, title='', description=''):
    order = project.experiments.count()

    return Experiment.objects.create(
        description=description,
        order=order,
        project=project,
        title=title or f'Experiment {order + 1}',
    )


def create_session(experiment, duration, title=''):
    order = experiment.sessions.count()

    return Session.objects.create(
        duration=duration,
        experiment=experiment,
        order=order,
        title=title or f'Session {order + 1}',
    )


def create_data_acquisition_method(session, type, location, stimulus=None):
    order = session.dataacquisitionmethods.count() + 1

    if isinstance(type, models.DataAcquisitionMethodType):
        pass
    elif isinstance(type, str):
        type = models.DataAcquisitionMethodType.objects.get(pk=type)
    else:
        raise ValueError('Unknown data type for `type` attribute')

    return DataAcquisitionMethod.objects.create(
        location=location,
        order=order,
        session=session,
        stimulus=stimulus,
        type=type,
    )


def get_experiments(project):
    return project.experiments.order_by('order')


def get_sessions(experiment):
    return experiment.sessions.order_by('order')


def get_data_acquisition_methods(session):
    return session.dataacquisitionmethods.order_by('order')


def get_data_acquisition_method_type(short_name):
    return models.DataAcquisitionMethodType.objects.get(short_name=short_name)


def update_experiment(experiment, **kwargs):
    updatable_fields = (
        'description',
        'title',
    )
    return update(experiment, updatable_fields, **kwargs)


def update_session(session, **kwargs):
    updatable_fields = (
        'duration',
        'setup_time',
        'teardown_time',
        'title',
    )
    return update(session, updatable_fields, **kwargs)


def update_data_acquisition_method(data_acquisition_method, **kwargs):
    updatable_fields = (
        'stimulus',
        'location',
    )
    return update(data_acquisition_method, updatable_fields, **kwargs)


def update(instance, updatable_fields, **kwargs):
    update_fields = []

    for field_name, value in kwargs.items():
        if field_name not in updatable_fields:
            raise ValueError(f'Cannot update field "{field_name}".')
        setattr(instance, field_name, value)
        update_fields.append(field_name)

    if update_fields:
        instance.save(update_fields=update_fields)

    return instance
