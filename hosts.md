<!-- hosts.md -->
---
layout: default
title: "Hosts"
---

<h1>Hosts</h1>
<ul>
{% assign host_list = "" | split: "" %}
{% for episode in site.episodes %}
  {% unless host_list contains episode.host %}
    {% assign host_list = host_list | push: episode.host %}
  {% endunless %}
{% endfor %}
{% for host in host_list %}
  <li>{{ host }}</li>
{% endfor %}
</ul>
