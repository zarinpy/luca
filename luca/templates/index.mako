<%inherit file="master.mako"/>
<%!
    from luca.i18n import gettext as _
%>
<%def name="title()">${settings.app_name}</%def>
<main>
  <h1>${settings.app_name}</h1>
  <p>${_("Server-rendered with FastAPI and Mako.")}</p>
</main>
