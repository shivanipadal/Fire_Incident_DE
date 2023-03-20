{#
    This macro returns the first 3 characters of month name
#}

{% macro extract_month_with_name(incidentmonth) -%}

    case {{ incidentmonth }}
        when 1 then 'Jan'
        when 2 then 'Feb'
        when 3 then 'Mar'
        when 4 then 'Apr'
        when 5 then 'May'
        when 6 then 'Jun'
        when 7 then 'Jul'
        when 8 then 'Aug'
        when 9 then 'Sep'
        when 10 then 'Oct'
        when 11 then 'Nov'
        when 12 then 'Dec'

    end

{%- endmacro %}