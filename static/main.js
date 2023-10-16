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

$("form").submit(function (event) {
  event.preventDefault();
  var id_person = $("#id_person").val();

  $.ajax({
    url: "/cari-laporan/hasil" + id_person,
    type: "GET",
    dataType: "html",
    success: function (htmlData) {
      $("#searched-data").html(htmlData);
    },
    error: function (error) {
      console.log(error);
    }
  });
});

var messages = {{ get_flashed_messages() | tojson | safe
}};

if (messages.length > 0) {
  alert(messages.join('\n'));
};

