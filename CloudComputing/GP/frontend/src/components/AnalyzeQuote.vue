<template>
    <div id="analyze-quote">

        <b-row>
            <b-col cols="5">
                <div class="quote">
                    <div class="quote_text">
                        <p>{{quote.text}}</p>
                    </div>
                </div>
                <span>
                <div class="flex-container">
                    <div style="flex-grow: 11">
                        <audio v-if="audio1" :src="audio1" controls></audio>
                    </div>
                    <div style="flex-grow: 1">
                        <b-button variant="primary" size="sm" @click="get_audio(quote.text, 1)"> Play</b-button>
                    </div>
                </div>

                </span>
            </b-col>
            <b-col cols="2">
                <b-form-select
                v-model="language"
                :options="languages"
                required
                ></b-form-select>
                <br>
                <br>
                <b-button v-if="quote" variant="primary" @click="translateText">Translate</b-button>
                

            </b-col>
            <b-col cols="5">
                 <b-alert v-model="showDismissibleAlert" variant="danger" dismissible>
                    <p>Please select language</p>
                </b-alert> 
                <div class="quote" v-if="translation">
                    <div class="quote_text" >
                        <p>{{translation}}</p>
                    </div>
                </div>
            </b-col>
        </b-row>
    </div>
</template>
<script>
export default {
    name: "AnalyzeQuote",
    props:{
        quote: Object
    },
    data()
    {
        return{
            languages:['Spanish', 'English'],
            language:null,
            text:null,
            showDismissibleAlert: false,
            translation:null,
            audio1:null,
            audio2:null

        }
    },
    methods:
    {
        translateText()
        {
            if (this.language===null)
            {
                this.showDismissibleAlert=true
                // alert("Please select Language")
                return;
            }
            let formData = new FormData();
            formData.append('language', this.language)
            let text = this.quote? this.quote.text: this.text
            formData.append('text', text)
            let config=  { 
                headers: {
                'Content-Type': 'multipart/form-data'
                }
            }
            this.$api.post('/analyze_text', formData, config).then((response)=>{
                this.translation = response.data["message"]
                })
        }
            ,
        get_audio(data, index)
        {
        let formData = new FormData();
        formData.append('text',  data);
        let config=  { 
            headers: {
            'Content-Type': 'multipart/form-data'
            },
            responseType: 'blob'
        }
        this.$api.post('/text_to_audio', formData, config).then((response)=>{
            console.log(response)
            // let audio = new Blob([response.data])
            // console.log(audio)
            if (index === 1)
            {   
                this.audio1 = URL.createObjectURL(response.data)
            }
            else{
                this.audio2 = URL.createObjectURL(response.data)
            }
            
            })
            
        }
    },

    
}
</script>

<style scoped>

#analyze-quote{
    margin-bottom: 50px;
    margin-top: 50px;
}
.quote{
    background-color: khaki;
    height: 120px;
    border-radius: 10px;
    box-shadow: 10px 5px 5px slategrey;
}
.quote_text{
        display: flex;
        height: 100%;
        margin: auto;
        align-items:center;
        justify-content:center;
}
.flex-container {
  display: flex;
  align-items: stretch;
  justify-content:center;
  align-items:center;
  margin-top: 20px;
}


</style>