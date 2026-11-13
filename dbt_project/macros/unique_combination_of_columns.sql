{% test unique_combination_of_columns(model, combination_of_columns) %}

SELECT
    {% for column in combination_of_columns %}
        {{ column }}{% if not loop.last %}, {% endif %}
    {% endfor %},
    COUNT(*) AS num_occurrences
FROM {{ model }}
GROUP BY
    {% for column in combination_of_columns %}
        {{ column }}{% if not loop.last %}, {% endif %}
    {% endfor %}
HAVING COUNT(*) > 1

{% endtest %}

