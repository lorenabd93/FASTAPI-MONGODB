var app=new Vue({
    el: '#app',
    data: {
        message:'Carsold !!!',
        info:[]
    },
    mounted(){
        axios.get("http://127.0.0.1:8000/").then(respuesta=>this.info=respuesta.data)
    },
});