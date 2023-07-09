$(function () {
  // Sizelist button
  var sz35 = document.getElementById("35");
  var sz35Checked = document.getElementById("size-35");
  sz35.addEventListener("change", function () {
    if (this.checked) {
      sz35Checked.style.display = "block";
    } else {
      sz35Checked.style.display = "none";
    }
  });

  var sz36 = document.getElementById("36");
  var sz36Checked = document.getElementById("size-36");
  sz36.addEventListener("change", function () {
    if (this.checked) {
      sz36Checked.style.display = "block";
    } else {
      sz36Checked.style.display = "none";
    }
  });

  var sz37 = document.getElementById("37");
  var sz37Checked = document.getElementById("size-37");
  sz37.addEventListener("change", function () {
    if (this.checked) {
      sz37Checked.style.display = "block";
    } else {
      sz37Checked.style.display = "none";
    }
  });

  var sz38 = document.getElementById("38");
  var sz38Checked = document.getElementById("size-38");
  sz38.addEventListener("change", function () {
    if (this.checked) {
      sz38Checked.style.display = "block";
    } else {
      sz38Checked.style.display = "none";
    }
  });

  var sz39 = document.getElementById("39");
  var sz39Checked = document.getElementById("size-39");
  sz39.addEventListener("change", function () {
    if (this.checked) {
      sz39Checked.style.display = "block";
    } else {
      sz39Checked.style.display = "none";
    }
  });

  var sz40 = document.getElementById("40");
  var sz40Checked = document.getElementById("size-40");
  sz40.addEventListener("change", function () {
    if (this.checked) {
      sz40Checked.style.display = "block";
    } else {
      sz40Checked.style.display = "none";
    }
  });

  var sz41 = document.getElementById("41");
  var sz41Checked = document.getElementById("size-41");
  sz41.addEventListener("change", function () {
    if (this.checked) {
      sz41Checked.style.display = "block";
    } else {
      sz41Checked.style.display = "none";
    }
  });

  var sz42 = document.getElementById("42");
  var sz42Checked = document.getElementById("size-42");
  sz42.addEventListener("change", function () {
    if (this.checked) {
      sz42Checked.style.display = "block";
    } else {
      sz42Checked.style.display = "none";
    }
  });

  var sz43 = document.getElementById("43");
  var sz43Checked = document.getElementById("size-43");
  sz43.addEventListener("change", function () {
    if (this.checked) {
      sz43Checked.style.display = "block";
    } else {
      sz43Checked.style.display = "none";
    }
  });

  var sz44 = document.getElementById("44");
  var sz44Checked = document.getElementById("size-44");
  sz44.addEventListener("change", function () {
    if (this.checked) {
      sz44Checked.style.display = "block";
    } else {
      sz44Checked.style.display = "none";
    }
  });

  var sz45 = document.getElementById("45");
  var sz45Checked = document.getElementById("size-45");
  sz45.addEventListener("change", function () {
    if (this.checked) {
      sz45Checked.style.display = "block";
    } else {
      sz45Checked.style.display = "none";
    }
  });

  var sz46 = document.getElementById("46");
  var sz46Checked = document.getElementById("size-46");
  sz46.addEventListener("change", function () {
    if (this.checked) {
      sz46Checked.style.display = "block";
    } else {
      sz46Checked.style.display = "none";
    }
  });

  var sz47 = document.getElementById("47");
  var sz47Checked = document.getElementById("size-47");
  sz47.addEventListener("change", function () {
    if (this.checked) {
      sz47Checked.style.display = "block";
    } else {
      sz47Checked.style.display = "none";
    }
  });

  // Set Currency
  var setCurrency = document.getElementById("currency");
  setCurrency.addEventListener("keyup", function (e) {
    setCurrency.value = formatRupiah(this.value, "Rp. ");
  });

  /* Formatter */
  function formatRupiah(angka, prefix) {
    var number_string = angka.replace(/[^,\d]/g, "").toString(),
      split = number_string.split(","),
      remain = split[0].length % 3,
      rupiah = split[0].substr(0, remain),
      threeDigit = split[0].substr(remain).match(/\d{3}/gi);

    if (threeDigit) {
      separator = remain ? "." : "";
      rupiah += separator + threeDigit.join(".");
    }

    rupiah = split[1] != undefined ? rupiah + "," + split[1] : rupiah;
    return prefix == undefined ? rupiah : rupiah ? "IDR " + rupiah : "";
  }

  // Upload Image
  jQuery(document).ready(function () {
    ImgUpload();
  });

  function ImgUpload() {
    var imgWrap = "";
    var imgArray = [];

    $(".upload__inputfile").each(function () {
      $(this).on("change", function (e) {
        imgWrap = $(this).closest(".upload__box").find(".upload__img-wrap");
        var maxLength = $(this).attr("data-max_length");

        var files = e.target.files;
        var filesArr = Array.prototype.slice.call(files);
        var iterator = 0;
        filesArr.forEach(function (f, index) {
          if (!f.type.match("image.*")) {
            return;
          }

          if (imgArray.length > maxLength) {
            return false;
          } else {
            var len = 0;
            for (var i = 0; i < imgArray.length; i++) {
              if (imgArray[i] !== undefined) {
                len++;
              }
            }
            if (len > maxLength) {
              return false;
            } else {
              imgArray.push(f);

              var reader = new FileReader();
              reader.onload = function (e) {
                var html =
                  "<div class='upload__img-box'><div style='background-image: url(" +
                  e.target.result +
                  ")' data-number='" +
                  $(".upload__img-close").length +
                  "' data-file='" +
                  f.name +
                  "' class='img-bg'><div class='upload__img-close'></div></div></div>";
                imgWrap.append(html);
                iterator++;
              };
              reader.readAsDataURL(f);
            }
          }
        });
      });
    });

    $("body").on("click", ".upload__img-close", function (e) {
      var file = $(this).parent().data("file");
      for (var i = 0; i < imgArray.length; i++) {
        if (imgArray[i].name === file) {
          imgArray.splice(i, 1);
          break;
        }
      }
      $(this).parent().parent().remove();
    });
  }

  // Semantic dropdown
  $(".ui.dropdown").dropdown();
});
