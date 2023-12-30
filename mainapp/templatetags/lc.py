from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe


register = template.Library()


TABLE_HEAD_START = """
                <table class="table linkRow">
                    </thead>
                        <tr>
                   """
TABLE_HEAD_END = """
                        </tr>
                    </thead>
                    <tbody>
                 """
TABLE_ROW_START = """
                        <tr {} style="{}">
                      """
TABLE_ROW_END = """
                        </tr>
                    """
TABLE_TAIL = """
                    </tbody>
                </table>
             """


TRAINING_STATUS = {
    'GREEN_mark': 'background-color: lawngreen;',
    'RED_mark' : 'background-color: crimson;',
    'WHITE_mark': ' ',
    'YELLOW_mark': 'background-color: gold;',
}


@register.simple_tag
def trainings_scheduler(schedule, header_tags, statuses, training_pks, is_trainer=None):        
    header = TABLE_HEAD_START
    for h_data in header_tags:
        header += "<th scope='col'><span style='font-size:100%'>{}</span></th>".format(h_data)
    header += TABLE_HEAD_END
    table_body = ''
    for row, status, training_pk in zip(schedule, statuses, training_pks):
        link = ''
        if is_trainer:
            link = "onclick=\"DoNav('" + reverse(
                'training_detail',
                kwargs={'training_pk': training_pk}
            ) + "')\""
        table_body += TABLE_ROW_START.format(
            link, TRAINING_STATUS[status]
        )
        for k, value in enumerate(row):
            table_body += "<td class='td-col-{}' style='min-width: 100px;'><span style='font-size:75%'>{}</span></td>".format(k, value)
        table_body += TABLE_ROW_END

    SCRIPT = """
        <script type="text/javascript">
            function DoNav(url) {
                document.location.href = url;
            }
        </script>
             """
    return mark_safe(header + table_body + TABLE_TAIL + SCRIPT)
