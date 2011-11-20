var URL = "http://wierzba.wzks.uj.edu.pl/~08_ciemborowicz/wykop_analytics/"

function chart(id, file, chart_title, x_title, y_title, callback) {  
  $.getJSON(URL + file, function(data) {
    
    chart = {
      chart: {
        renderTo: id,
        type: 'column'
      },
      title: {
        text: chart_title
      },
      yAxis: {
        title: {
          text: y_title
        }
      },
      xAxis: {
        title: {
          text: x_title
        },
        categories: data.keys
      },
      series: [{
          name: 'wykopane',
          data: data.promoted
        }, {
          name: 'niewykopane',
          data: data.upcoming
        }
      ]
    }
    callback(chart)
  });
}

var hour_occurrences
var day_occurrences
var month_occurrences
/*
var hour_comparision = new Chart(); 
var day_comparision = new Chart(); 
var month_comparision = new Chart(); 
*/

$(document).ready(function() {
  chart('hour_occurrences',
        'hour.json',
        'Godzinne zestawienie ilości znalezisk',
        'godzina',
        'ilość wykopów',
        function(chart) {
          hour_occurrences = new Highcharts.Chart(chart)
        }
  );
  chart('day_occurrences',
        'day.json',
        'Dzienne zestawienie ilości znalezisk',
        'dzień',
        'ilość wykopów',
        function(chart) {
          day_occurrences = new Highcharts.Chart(chart)
        }
  );
  chart('month_occurrences',
        'month.json',
        'Miesięczne zestawienie ilości znalezisk',
        'miesiąc',
        'ilość wykopów',
        function(chart) {
          month_occurrences = new Highcharts.Chart(chart)
        }
  );
});
