$(document).ready(function(){
    console.log('jquery')
    var easy = document.getElementById("easyPercent")
    var medium = document.getElementById("mediumPercent")
    var hard = document.getElementById("hardPercent")
    var elite = document.getElementById("elitePercent")
    var master = document.getElementById("masterPercent")
    var passive = document.getElementById("passivePercent")
    var extra = document.getElementById("extraPercent")
    var pets = document.getElementById("petsPercent")
    var tiers = [easy, medium, hard, elite, passive,extra, pets]

    for (let i = 0; i < tiers.length; i++) {
        let value = parseInt(tiers[i].innerHTML);
        console.log(value)
        console.log(typeof(value))
        if (value === 0){
            tiers[i].classList.add("percent_red");
        }
        else if (value <= 24){
            tiers[i].classList.add("percent_orange_red");
        }
        else if (value <= 49){
            tiers[i].classList.add("percent_orange");
        }
        else if (value <= 74){
            tiers[i].classList.add("percent_yellow");
        }
        else if (value <= 99){
            tiers[i].classList.add("percent_yellow_green");
        }
        else if (value === 100){
            tiers[i].classList.add("percent_green");
        }
    }
  });