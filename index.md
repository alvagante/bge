---
layout: default
title: "Home"
---

<h1>{{ site.title }}</h1>

<h2>Ultimo Episodio</h2>

{% assign latest_episode = site.episodes | first %}
<h3><a href="{{ latest_episode.url | relative_url }}">{{ latest_episode.title }}</a></h3>
<p>{{ latest_episode.description }}</p>
<a href="{{ latest_episode.url | relative_url }}">Ascolta l'episodio</a>

<p><a href="/episodes/">Guarda tutti gli episodi</a></p>
