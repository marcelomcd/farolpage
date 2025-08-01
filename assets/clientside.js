window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        redirectTo: function (path) {
            if (path) {
                window.location.href = path;
            }
            return '';
        },

        abrirNovaAba: function (active_cell, data) {
            if (!active_cell || !data || !data[active_cell.row])
                return window.dash_clientside.no_update;
            const id = data[active_cell.row].ID;
            if (id) {
                const url = `/feature?id=${id}`;
                window.open(url, '_blank');
            }
            return `/feature?id=${id}`;
        }
    }
});
