{% extends "!autosummary/module.rst" %}
asdasd

   {% block functions %}
   {% if functions %}
   .. rubric:: Functions

   {% for item in functions %}
   .. autofunction:: {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

