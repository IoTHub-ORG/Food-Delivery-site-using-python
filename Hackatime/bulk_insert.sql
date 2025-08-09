{% extends "base.html" %}
{% block content %}
<h2>Restaurants</h2>
<ul class="list-group">
  {% for r in restaurants %}
    <li>
      <a class="btn" href="{{ url_for('restaurant', rest_id=r.id) }}">
        {{ r.name }}
      </a>
      <span class="description">{{ r.description }}</span>
    </li>
  {% endfor %}
</ul>
<a class="btn btn-secondary" href="{{ url_for('logout') }}">Logout</a>
{% endblock %}
