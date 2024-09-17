<!-- guests.md -->
---
layout: default
title: "Guests"
---

<h1>Guests</h1>
<ul>
{% assign guest_list = "" | split: "" %}
{% for episode in site.episodes %}
  {% for guest in episode.guests %}
    {% unless guest_list contains guest %}
      {% assign guest_list = guest_list | push: guest %}
    {% endunless %}
  {% endfor %}
{% endfor %}
{% for guest in guest_list %}
  <li>{{ guest }}</li>
{% endfor %}
</ul>
