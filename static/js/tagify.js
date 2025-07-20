var input = document.querySelector('#tagsInput');

var tagify = new Tagify(input, {
  whitelist: [
    {% for tag in tags %}
      "{{ tag.name }}",
    {% endfor %}
  ],
  dropdown: {
    enabled: 1,
    maxItems: 10,
    classname: "tags-look",
    closeOnSelect: false
  }
});
