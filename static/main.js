$(document).ready(function () {
    

    $("#laporan-form").submit(function (e) {
        var nama = $("[name=nama]").val();
        var noWa = $("[name=no-wa]").val();
        var idDiscord = $("[name=id-discord]").val();
        var jenisL = $("[name=jenis-l]").val();
        var laporan = $("[name=laporan]").val();

        if (!nama || !noWa || !idDiscord || !jenisL || !laporan) {
            e.preventDefault();
            alert('Semua kolom harus diisi.');
        }
    });

    $("form").submit(function(event) {
        event.preventDefault();
        var id_person = $("#id_person").val();
        
        $.ajax({
            url: "/cari-laporan/hasil" + id_person,
            type: "GET",
            dataType: "html",
            success: function(htmlData) {
                $("#searched-data").html(htmlData);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

});
var messages = {{ get_flashed_messages() | tojson | safe
}};

if (messages.length > 0) {
    alert(messages.join('\n'));
};
if (performance.navigation.type === 1) {
    window.location.href = '/laporan';
}

google.charts.load('current', {packages: ['corechart', 'bar']});
google.charts.setOnLoadCallback(drawBasic);

function drawBasic() {

      var data = new google.visualization.DataTable();
      data.addColumn('timeofday', 'Time of Day');
      data.addColumn('number', 'Motivation Level');

      data.addRows([
        [{v: [8, 0, 0], f: '8 am'}, 1],
        [{v: [9, 0, 0], f: '9 am'}, 2],
        [{v: [10, 0, 0], f:'10 am'}, 3],
        [{v: [11, 0, 0], f: '11 am'}, 4],
        [{v: [12, 0, 0], f: '12 pm'}, 5],
        [{v: [13, 0, 0], f: '1 pm'}, 6],
        [{v: [14, 0, 0], f: '2 pm'}, 7],
        [{v: [15, 0, 0], f: '3 pm'}, 8],
        [{v: [16, 0, 0], f: '4 pm'}, 9],
        [{v: [17, 0, 0], f: '5 pm'}, 10],
      ]);

      var options = {
        title: 'Motivation Level Throughout the Day',
        hAxis: {
          title: 'Time of Day',
          format: 'h:mm a',
          viewWindow: {
            min: [7, 30, 0],
            max: [17, 30, 0]
          }
        },
        vAxis: {
          title: 'Rating (scale of 1-10)'
        }
      };

      var chart = new google.visualization.ColumnChart(
        document.getElementById('chart_div'));

      chart.draw(data, options);
    }