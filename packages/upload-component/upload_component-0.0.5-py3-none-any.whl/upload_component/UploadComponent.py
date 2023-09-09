# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class UploadComponent(Component):
    """An UploadComponent component.


Keyword arguments:

- id (string; default "my-file-uploader")

- baseurl (string; default 'https://athena.rc.ufl.edu/api/v1')

- fileTypeFlag (boolean; default False)

- filetypes (list of strings; default ["svs", "ndpi", "scn", "tiff", "qptiff", "tif"])

- girderToken (string; default "uZ4L8ceMqynhMKsmrPZpen5QUQMu6Uvy4nqlpMRhyilby3YZV79FZlQp9nhAxqd3")

- parentId (string; default "647f32c9435c92704a565d1b")

- statusCode (number; default 200)

- uploadComplete (boolean; default False)"""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'upload_component'
    _type = 'UploadComponent'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, uploadComplete=Component.UNDEFINED, statusCode=Component.UNDEFINED, baseurl=Component.UNDEFINED, girderToken=Component.UNDEFINED, parentId=Component.UNDEFINED, filetypes=Component.UNDEFINED, fileTypeFlag=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'baseurl', 'fileTypeFlag', 'filetypes', 'girderToken', 'parentId', 'statusCode', 'uploadComplete']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'baseurl', 'fileTypeFlag', 'filetypes', 'girderToken', 'parentId', 'statusCode', 'uploadComplete']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(UploadComponent, self).__init__(**args)
