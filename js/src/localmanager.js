import ts from 'treibstoff';

export function autocomplete_gid(request, callback) {
    ts.ajax.request({
        success: function(data) {
            callback(data);
        },
        url: 'group_id_vocab',
        params: {
            term: request.term
        },
        type: 'json'
    });
}
