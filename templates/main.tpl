<!DOCTYPE html>
<html>
<head lang="sk">
<meta charset="utf-8">
<title>{{ product_name }}</title>
</head>
<style>

.main {

width: 58mm;
height: 195mm;
display: inline-block;
margin: 0;
vertical-align: middle;
border: 1px solid black;
text-align: justify;
padding: 0 1mm;
box-sizing: border-box;
}

.padding {
    padding: 5px;
}
#image {  
width: 20mm;  
height: auto; 
border: 1px solid black;
align: middle;
} 


.regtext {

font-size: 0.7em;
font-family:Calibri, sans-serif; 
font-style:normal; 
font-variant:; 
font-weight:normal; 



}

.title {
   font-family:"Gill Sans MT Ext Condensed Bold", fantasy;
   font-style:; 
   font-variant:; 
   font-weight:bold; 
   font-size:25px;
   color: red;
   text-align: center;
   margin: 0;
}


.nav3 {
    
    height: auto;
    width: 200px;
    float: left;
    padding: 1px;
    font-family: Arial, Helvetica, sans-serif;
    margin: 0;

    
}


#icons{
    display:inline-block;
    width: 18%; 
    height: 18%; 
    
    
   }


</style>

<body>
<div>


<div class="main">
    
    
    <!-- Logo Company image: -->
    <div  class="padding" align="middle">
        <img id="image" src="https://t3.ftcdn.net/jpg/01/04/31/94/160_F_104319472_twkUYWSOvHPFsQyFHVzf2QssyPXFoPuX.jpg" alt=\"Smiley face\">
    </div>


    <!-- Title: -->
    <p class="title" >{{ product_name }}</P>
    
         <!-- This div is heare just because of regular text -->
         <div class="regtext">

            <br>
            Plnený/obložený pekárenský výrobok<br>
            <b><u>Zloženie:</u></b><br>

                {% for key,value in items.iterrows() %}
                      <b>{{ value['_products'] }}: </b> {{ value['desc_from_library'] }}
                {% endfor %}


            <br>
            <b>Alergény:</b>
              {% for key,value in items.iterrows() %}

                  {% if value['alergens'] != ' ' %}
                      {{ value['alergens'] }},
                  {% endif %}

                {% endfor %}

            . Môže obsahovať:
             {% for key,value in items.iterrows() %}
                  {% if value['can_have'] != ' ' %}
                    {{ value['can_have'] }},
                  {% endif %}

             {% endfor %}
.
            <b><br>GMO: </b>výrobok neobsahuje GMO
            <br>
            <b>Energetická hodnota v 100g: </b> {{kj}} kJ/ {{kcal}} kcal;
            Tuk {{ en_value['Tuk'] }} g;
            Nasytené mastné kyseliny {{ en_value['Nenásytené mastné kyseliny'] }} g;
            Sacharidy {{ en_value['Sacharidy'] }}  g;
            Cukry {{ en_value['Cukry'] }} g;
            Bielkoviny {{ en_value['Bielkoviny'] }} g;
            Soľ {{ en_value['Soľ'] }} g.

            <br>
            <br>
            Vyrába: <b>Two Wings s.r.o.</b>, 
            Letisko Košice, 04175 Košice; 
            prevádzka: Pri bitúnku 2, Košice. 
            Dátum spotreby je číslo šarže. 
            Množstvo/Hmotnosť: {{ total_product_weight }}.
            Krajina pôvodu: Slovenská republika. 
            Balené v ochrannej atmosfére. 
            Skladujte v chlade pri teplote:  2-4°C. 
            Po otvorení skonzumujte ihneď, 
            alebo najneskôr do 1 hodiny.  
            Spotrebujte do:

        

        </div>
        
   
        <div class="nav3">
           <!-- Person: -->
           <img id="icons" src="https://image.freepik.com/free-icon/recycle-symbol_318-32031.jpg">
           <!-- Recycle: -->
            <img id="icons" src="http://www.vectorportal.com/img_novi/pp5_6860.jpg">
           
        </div>
        
        
        

</div>

                                                                                                                                     
</div>




</body>
</html>
