

var endpoint = '/api/employee/dep/'
$.ajax({
    method: "GET",
    url: endpoint,
    success: function(data){
        obj = data.obj
        legend = 'DISTRIBUISAUN FUNSIONARIO TUIR EKIPA'
        categories = data.label
        setEmpDep()
    },
    error: function(error_data){
        console.log("error")
        console.log(error_data)
    }
})

function setEmpDep(){
    Highcharts.chart('setEmpDep', {
        colors: ['#01BAF2', '#71BF45', '#FAA74B', '#B37CD2', '#d42c06', '#dbde23', '#68d9d7'],
    chart: {
        type: 'pie'
    },
    accessibility: {
        point: {
            valueSuffix: '%'
        }
    },
    title: {
        text: legend
    },
    tooltip: {
        formatter: function () {
            return this.point.name + ': ' + this.y;
        }
    },
    plotOptions: {
        pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
                enabled: true,
                formatter: function () {
                    return this.point.name + ': ' + this.y;
                }
            },
            showInLegend: true
        }
    },
    credits: {
        enabled: false
  },
    series: [{
        name: 'Registrations',
        colorByPoint: true,
        innerSize: '75%',
        data: obj
    }]
    });


}




