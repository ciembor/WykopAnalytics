var URL = "http://wierzba.wzks.uj.edu.pl/~08_ciemborowicz/wykop_analytics/"

function keysToCategories(keys, name) {
  
  if (name === 'day') {
    categories = ['podziedziałek', 'wtorek', 'środa', 'czwartek', 'piątek', 'sobota', 'niedziela'];
  }
  else if (name === 'month') {
    categories = ['styczeń', 'luty', 'marzec', 'kwiecień', 'maj', 'czerwiec', 'lipiec', 'sierpień', 'wrzesień', 'październik', 'listopad', 'grudzień'];
  }
  else {
    categories = keys;
  }
  
  return categories
  
}

////////////////////////////////////////////////////////////////////////

Highcharts.setOptions({
  colors: [
    '#f58237', 
    '#367aa9', 
    '#69dc3e', 
    '#f24459', 
  ],
  credits: {
    enabled: false
  },
  legend: {
    align: 'right',
    x: -10,
    verticalAlign: 'top',
    y: -3,
    floating: true,
    backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColorSolid) || 'white',
    borderColor: '#CCC',
    borderWidth: 1,
    shadow: false
  },
  plotOptions: {
    column: {
      stacking: 'normal',
      borderWidth: 0,
      shadow: false
    }
  },
  title: {
    align: "left",
    x: 63,
    style: {
      color: "#000000",
      "font-weight": "bold"
    }
  }
});

////////////////////////////////////////////////////////////////////////

function Chart(id, name, chart_title, x_title, y_title, data) {  
  
  return {
    chart: {
      renderTo: id,
      type: 'column'
    },
    title: {
      text: chart_title
    },
    yAxis: {
      title: {
        text: y_title,
        style: {
          color: "#000000"
        }
      }
    },
    xAxis: {
      title: {
        text: x_title,
        style: {
          color: "#000000"
        }
      },
      categories: keysToCategories(data.keys, name)
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
  
}

////////////////////////////////////////////////////////////////////////

function ComparisionChart(id, name, chart_title, x_title, y_title, data) {  
  
  var comparision = new Array();
  var len = data.keys.length;
  
  for (var i = 0; i < len; i++) {
    if (data.upcoming[i]) {
      comparision[i] = Math.round((data.promoted[i] / data.upcoming[i]) * 1000) / 1000;
    }
    else {
      comparision[i] = 0; // null?
    }
  }
  
  return {
    chart: {
      renderTo: id,
      type: 'column'
    },
    title: {
      text: chart_title
    },
    legend: {
      enabled: false
    },
    colors: [
      '#239d85',
      '#9ae133',
      '#ce2e77',
      '#69dc3e', 
      '#f24459', 
      '#f58237', 
      '#367aa9'
    ],
    yAxis: {
      title: {
        text: y_title,
        style: {
          color: "#000000"
        }
      },
      max: 1
    },
    xAxis: {
      title: {
        text: x_title,
        style: {
          color: "#000000"
        }
      },
      categories:  keysToCategories(data.keys, name)
    },
    series: [{
        data: comparision
    }]
  }
  
}

////////////////////////////////////////////////////////////////////////

var hour_occurrences
var day_occurrences
var month_occurrences
var hour_comparision
var day_comparision
var month_comparision

$(document).ready(function() {

  $.ajax({
    type: "GET",
    url: URL + "results.js", 
    dataType: "jsonp",
    crossDomain: true,
    jsonpCallback: 'response',
    success: function(data) {
      
      hour_occurrences = new Highcharts.Chart(new Chart('hour_occurrences',
                                                         'hour',
                                                         'Suma znalezisk dodanych o określonej godzinie',
                                                         'godzina',
                                                         'liczba znalezisk',
                                                         data['hour']));
                                                         
      day_occurrences = new Highcharts.Chart(new Chart('day_occurrences',
                                                         'day',
                                                         'Suma znalezisk dodanych w określonym dniu tygodnia',
                                                         'dzień',
                                                         'liczba znalezisk',
                                                         data['day']));
                                                         
      month_occurrences = new Highcharts.Chart(new Chart('month_occurrences',
                                                         'month',
                                                         'Suma znalezisk dodanych w określonym miesiącu',
                                                         'miesiąc',
                                                         'liczba znalezisk',
                                                         data['month']));
      
      hour_comparision = new Highcharts.Chart(new ComparisionChart('hour_comparision',
                                                                    'hour',
                                                                    'Prawdopodobieństwo wejścia znaleziska na stronę główną w zależności od godziny dodania',
                                                                    'godzina',
                                                                    'prawdopodobieństwo',
                                                                    data['hour']));
                                                         
      day_comparision = new Highcharts.Chart(new ComparisionChart('day_comparision',
                                                                   'day',
                                                                   'Prawdopodobieństwo wejścia znaleziska na stronę główną w zależności od dnia tygodnia dodania',
                                                                   'dzień',
                                                                   'prawdopodobieństwo',
                                                                   data['day']));
                                                         
      month_comparision = new Highcharts.Chart(new ComparisionChart('month_comparision',
                                                                     'month',
                                                                     'Prawdopodobieństwo wejścia znaleziska na stronę główną w zależności od miesiąca dodania',
                                                                     'miesiąc',
                                                                     'prawdopodobieństwo',
                                                                     data['month']));
    }
  })  

});
