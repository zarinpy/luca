<%def name="title()">Luca</%def>
<%!
    from luca.i18n import DEFAULT_CODE
%>
<!doctype html>
<html lang="${DEFAULT_CODE}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>${self.title()}</title>
  </head>
  <body>
    ${self.body()}
  </body>
</html>
