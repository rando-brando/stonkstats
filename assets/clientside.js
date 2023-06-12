window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        reactive_search: function(query, data) {
            if(query) {
                var df = JSON.parse(data)
                var filteredData = df.filter(function(row) {
                    var search = query.toLowerCase()
                    var symbol = row.symbol.toLowerCase()
                    var name = row.companyName.toLowerCase()
                    if (symbol.includes(search) || name.includes(search)) {
                        return row;
                    }
                })
                var rows = filteredData.map(function(row) {
                    return {
                        'type': 'Tr',
                        'namespace': 'dash_html_components',
                        'props': {
                            'class': 'search-row',
                            'children': [
                                {
                                    'type': 'Td',
                                    'namespace': 'dash_html_components',
                                    'props': {
                                        'class': 'symbol',
                                        'children': row.symbol,
                                    }
                                },
                                {
                                    'type': 'Td',
                                    'namespace': 'dash_html_components',
                                    'props': {
                                        'class': 'company',
                                        'children': row.companyName
                                    }
                                },
                                {
                                    'type': 'Td',
                                    'namespace': 'dash_html_components',
                                    'props': {
                                        'class': 'exchange',
                                        'children': row.exchangeShortName
                                    }
                                }
                            ]
                        }
                    }
                })
                return {
                    'type': 'Tbody',
                    'namespace': 'dash_html_components',
                    'props': {
                        'class': 'search-table-active',
                        'children': rows
                    }
                }
            }
            return {
                'type': 'Tbody',
                'namespace': 'dash_html_components',
                'props': {'class': 'search-table-inactive'}
            }
        }
    }
});