from cone.app import security
from cone.app.browser.actions import LinkAction
from cone.app.browser.ajax import AjaxEvent
from cone.app.browser.ajax import AjaxMessage
from cone.app.browser.ajax import AjaxPath
from cone.app.browser.authoring import _FormRenderingTile
from cone.app.browser.authoring import ContentForm
from cone.app.browser.authoring import render_form
from cone.app.browser.form import Form
from cone.app.browser.layout import personal_tools_action
from cone.app.browser.utils import make_query
from cone.app.browser.utils import make_url
from cone.app.ugm import principal_data
from cone.app.ugm import ugm_backend
from cone.app.utils import node_path
from cone.tile import tile
from cone.ugm.browser.principal import password_settings
from cone.ugm.model.user import User
from node.utils import UNSET
from plumber import plumbing
from pyramid.i18n import get_localizer
from pyramid.i18n import TranslationStringFactory
from pyramid.view import view_config
from yafowil.base import ExtractionError
from yafowil.base import factory


_ = TranslationStringFactory('cone.ugm')


@personal_tools_action(name='change_password')
class ChangePasswordAction(LinkAction):
    text = _('change_password', default='Change Password')
    icon = 'glyphicons glyphicons-keys'
    event = 'contextchanged:#layout'
    path = 'href'

    @property
    def display(self):
        return ugm_backend.ugm is not None and \
            self.request.authenticated_userid not in [security.ADMIN_USER, None]

    @property
    def href(self):
        return make_url(
            self.request,
            node=self.model.root['users'][self.request.authenticated_userid],
            resource='change_password'
        )

    @property
    def target(self):
        return make_url(
            self.request,
            node=self.model.root['users'][self.request.authenticated_userid],
            query=make_query(contenttile='change_password')
        )


@view_config(
    name='change_password',
    context=User,
    permission='change_own_password')
def change_password(model, request):
    return render_form(model, request, 'change_password')


@tile(
    name='change_password',
    interface=User,
    permission='change_own_password')
class ChangePasswordTile(_FormRenderingTile):
    form_tile_name = 'change_password_form'


@tile(
    name='change_password_form',
    interface=User,
    permission='change_own_password')
@plumbing(ContentForm)
class ChangePasswordForm(Form):
    show_contextmenu = False

    @property
    def form_heading(self):
        userid = self.request.authenticated_userid
        data = principal_data(userid)
        user = data.get('fullname', userid)
        localizer = get_localizer(self.request)
        return localizer.translate(_(
            'change_user_password',
            default='Change Password: ${user}',
            mapping={'user': user}
        ))

    def prepare(self):
        action = make_url(
            self.request,
            node=self.model,
            resource='change_password'
        )
        form = factory(
            u'form',
            name='change_password_form',
            props={
                'action': action,
                'class': 'form-horizontal',
            })
        current_password_props = {
            'required': _('no_password_given', default='No password given'),
            'label': _('current_password', default='Current Password'),
            'label.class_add': 'col-sm-2',
            'div.class_add': 'col-sm-10',
        }
        current_password_props.update(password_settings())
        form['current_password'] = factory(
            'field:label:div:*current_password_matches:error:password',
            props=current_password_props,
            custom={
                'current_password_matches': {
                    'extractors': [self.current_password_matches]
                }
            })
        new_password_props = {
            'required': _('no_password_given', default='No password given'),
            'label': _('new_password', default='New Password'),
            'label.class_add': 'col-sm-2',
            'div.class_add': 'col-sm-10',
        }
        new_password_props.update(password_settings())
        form['new_password'] = factory(
            'field:label:div:error:password',
            props=new_password_props)
        confirm_password_props = {
            'required': _('no_password_given', default='No password given'),
            'label': _('confirm_password', default='Confirm Password'),
            'label.class_add': 'col-sm-2',
            'div.class_add': 'col-sm-10',
        }
        confirm_password_props.update(password_settings())
        form['confirm_password'] = factory(
            'field:label:div:*confirm_password_matches:error:password',
            props=confirm_password_props,
            custom={
                'confirm_password_matches': {
                    'extractors': [self.confirm_password_matches]
                }
            })
        form['change'] = factory('#button', props={
            'action': 'change',
            'expression': True,
            'handler': self.change_password,
            'next': self.next,
            'label': _('change_password', default='Change Password'),
        })
        self.form = form

    def current_password_matches(self, widget, data):
        extracted = data.extracted
        if extracted is UNSET:
            return extracted
        user = security.authenticated_user(self.request)
        if not user.authenticate(extracted):
            raise ExtractionError(
                _('wrong_password', default='Wrong Password')
            )
        return extracted

    def confirm_password_matches(self, widget, data):
        confirm_password = data.extracted
        if confirm_password is UNSET:
            return confirm_password
        new_password = data.parent['new_password'].extracted
        if confirm_password != new_password:
            raise ExtractionError(
                _('password_missmatch', default='Password Mismatch')
            )
        return confirm_password

    def change_password(self, widget, data):
        def fetch(name):
            dottedpath = 'change_password_form.{0}'.format(name)
            return data.fetch(dottedpath).extracted
        user = security.authenticated_user(self.request)
        current_password = fetch('current_password')
        new_password = fetch('new_password')
        user.passwd(
            current_password.encode('utf-8'),
            new_password.encode('utf-8')
        )
        user.parent.parent()

    def next(self, request):
        localizer = get_localizer(self.request)
        text = localizer.translate(
            _('password_changed', default='Password change successful')
        )
        url = make_url(self.request, node=self.model.root)
        path = '/'.join(node_path(self.model.root))
        return [
            AjaxMessage(text, 'message', None),
            AjaxPath(path, target=url, event='contextchanged:#layout'),
            AjaxEvent(url, 'contextchanged', '#layout')
        ]
