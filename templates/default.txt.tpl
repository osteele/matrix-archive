{% for message in messages -%}
{%- set content = message.content -%}
From {{ message.sender }}
Date {{ message.timestamp }}
{% if content.msgtype == 'm.text' %}
{{ content.body }}
{%- elif content.msgtype == 'm.image' -%}
Image: {{ content.url }}
{%- else -%}
Unknown type: {{ content.msgtype }}
{%- endif %}
---
{% endfor %}
