//const xValues = ["2023-12-04", "2023-12-05","2023-12-06","2023-12-07","2023-12-08","2023-12-09","2023-12-10",
//"2023-12-11","2023-12-12","2023-12-13","2023-12-14","2023-12-15","2023-12-16","2023-12-17","2023-12-18","2023-12-19",
//"2023-12-20","2023-12-21","2023-12-22","2023-12-23","2023-12-24","2023-12-25","2023-12-26","2023-12-27","2023-12-28",
//"2023-12-29","2023-12-30","2023-12-31","2024-01-01","2024-01-02"];
//const yValues = [0,0,0,0,0,49,84,171,736,1944,12998,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];

async function update_chart(chart, data_name){
  var url = '/stats/'+data_name;
  var xValues = [];
  var yValues = [];
  try {
    json_obj = await (await fetch(url)).json();
    xValues = json_obj["xValues"];
    yValues = json_obj["yValues"];
  } catch(e) {
    console.log('error');
  } 
  chart.data.labels = xValues;
  chart.data.datasets[0].data = yValues;
  chart.update();
}

var chart_2ch_hk = new Chart("2ch_hk_chart", {
  type: "bar",
  data: {
    labels: [],
    datasets: [{
      backgroundColor: "blue",
      data: []
    }]
  },
  options: {
    legend: {display: false},
    title: {
      display: true,
      text: "2ch.hk for day"
    },
    scales: {
        yAxes: [{
        ticks: {
            beginAtZero: true
        }
        }]
    }
  }
});

window.onload = function() {
  update_chart(chart_2ch_hk, "2ch_hk_b_1h_1d");
};
