%if len(rows)>0:
<table class="pure-table pure-table-bordered">
    <thead>
        <tr>
            %for col in rows[0]:
                <th>{{col}}</th>
            %end
        </tr>
    </thead>
    <tbody>
    %for i, row in enumerate(rows):
        %if i%2 == 0:
        <tr class="pure-table-even">
        %else:
        <tr class="pure-table-odd">
        %end
            %for attr in row:
                <td>
                    %if row[attr]:
                        %if isinstance(row[attr], list):
                            %include('make_table',rows=row[attr], title="")
                        %else:
                        {{row[attr]}}
                        %end
                    %end
                </td>
            %end
        </tr>
    %end
    </tbody>
</table>
%else:
<h3>NO DATA!</h3>
%end