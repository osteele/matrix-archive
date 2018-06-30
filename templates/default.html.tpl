<meta charset="UTF-8">
{% for message in messages %}
{% set content = message.content %}
<div class="message">
  <dl>
  <dt>From</dt>
  <dd>{{ message.sender }}</dd>
  <dt>Date</dt>
  <dd>{{ message.timestamp }}</dd>
  </dl>
{% if content.msgtype == 'm.text' %}
  <div class="body">{{ content.body }}</div>
{% elif content.msgtype == 'm.image' %}
  <div class="body"><img src="{{ content.url }}" /></div>
{% else %}
  <div class="error">Unknown message type<div>
{% endif %}
</div>
{% endfor %}
