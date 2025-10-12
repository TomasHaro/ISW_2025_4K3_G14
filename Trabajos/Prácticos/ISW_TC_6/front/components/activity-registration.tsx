"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Clock, Users, AlertCircle, CheckCircle2, Leaf } from "lucide-react"

// Mock data - replace with your backend API calls
const activities = [
  {
    id: "tirolesa",
    name: "Tirolesa",
    description: "Deslízate por las copas de los árboles en una aventura emocionante",
    requiresClothingSize: true,
    availableSlots: [
      { time: "09:00", available: 8 },
      { time: "11:00", available: 5 },
      { time: "14:00", available: 0 },
      { time: "16:00", available: 12 },
    ],
    terms:
      "Los participantes deben tener al menos 12 años y pesar menos de 120kg. Se requiere calzado cerrado y ropa cómoda. El equipo de seguridad será proporcionado por el parque.",
  },
  {
    id: "safari",
    name: "Safari",
    description: "Recorre el parque en vehículo y conoce a nuestros animales de cerca",
    requiresClothingSize: false,
    availableSlots: [
      { time: "10:00", available: 15 },
      { time: "12:00", available: 8 },
      { time: "15:00", available: 10 },
      { time: "17:00", available: 6 },
    ],
    terms:
      "No se permite alimentar a los animales. Los niños menores de 5 años deben ir acompañados de un adulto. Se recomienda llevar protector solar y sombrero.",
  },
  {
    id: "palestra",
    name: "Palestra",
    description: "Desafía tus habilidades en nuestro muro de escalada natural",
    requiresClothingSize: true,
    availableSlots: [
      { time: "09:30", available: 6 },
      { time: "11:30", available: 4 },
      { time: "14:30", available: 7 },
      { time: "16:30", available: 0 },
    ],
    terms:
      "Edad mínima 10 años. Se proporcionará todo el equipo de seguridad. Los participantes deben firmar un formulario de consentimiento. No se permite escalar con objetos sueltos.",
  },
  {
    id: "jardineria",
    name: "Jardinería",
    description: "Aprende sobre plantas nativas y ayuda en nuestro jardín botánico",
    requiresClothingSize: false,
    availableSlots: [
      { time: "08:00", available: 20 },
      { time: "10:30", available: 15 },
      { time: "13:00", available: 18 },
      { time: "15:30", available: 12 },
    ],
    terms:
      "Actividad apta para todas las edades. Se recomienda usar ropa que pueda ensuciarse. Se proporcionarán guantes y herramientas. Los niños menores de 8 años deben estar acompañados.",
  },
]

interface Participant {
  name: string
  dni: string
  age: string
  clothingSize?: string
}

export function ActivityRegistration() {
  const [step, setStep] = useState(1)
  const [selectedActivity, setSelectedActivity] = useState<string>("")
  const [selectedTime, setSelectedTime] = useState<string>("")
  const [participantCount, setParticipantCount] = useState<string>("1")
  const [participants, setParticipants] = useState<Participant[]>([{ name: "", dni: "", age: "", clothingSize: "" }])
  const [termsAccepted, setTermsAccepted] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const currentActivity = activities.find((a) => a.id === selectedActivity)
  const selectedSlot = currentActivity?.availableSlots.find((s) => s.time === selectedTime)

  const handleActivitySelect = (activityId: string) => {
    setSelectedActivity(activityId)
    setSelectedTime("")
    setStep(2)
  }

  const handleTimeSelect = (time: string) => {
    setSelectedTime(time)
  }

  const handleParticipantCountChange = (count: string) => {
    const numCount = Number.parseInt(count) || 1
    setParticipantCount(count)

    const newParticipants = Array.from(
      { length: numCount },
      (_, i) => participants[i] || { name: "", dni: "", age: "", clothingSize: "" },
    )
    setParticipants(newParticipants)
  }

  const updateParticipant = (index: number, field: keyof Participant, value: string) => {
    const newParticipants = [...participants]
    newParticipants[index] = { ...newParticipants[index], [field]: value }
    setParticipants(newParticipants)
  }

  const canProceedToStep3 = selectedActivity && selectedTime && selectedSlot && selectedSlot.available > 0

  const canSubmit = () => {
    if (!termsAccepted) return false

    return participants.every((p) => {
      const basicFieldsFilled = p.name && p.dni && p.age
      if (!currentActivity?.requiresClothingSize) return basicFieldsFilled
      return basicFieldsFilled && p.clothingSize
    })
  }

  const handleSubmit = () => {
    if (canSubmit()) {
      // Here you would call your backend API
      console.log("Submitting registration:", {
        activity: selectedActivity,
        time: selectedTime,
        participants,
      })
      setSubmitted(true)
    }
  }

  const resetForm = () => {
    setStep(1)
    setSelectedActivity("")
    setSelectedTime("")
    setParticipantCount("1")
    setParticipants([{ name: "", dni: "", age: "", clothingSize: "" }])
    setTermsAccepted(false)
    setSubmitted(false)
  }

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-primary/5 via-accent/5 to-secondary/10">
        <Card className="max-w-md w-full">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
              <CheckCircle2 className="w-10 h-10 text-primary" />
            </div>
            <CardTitle className="text-2xl">¡Inscripción Exitosa!</CardTitle>
            <CardDescription className="text-base">
              Tu reserva para {currentActivity?.name} a las {selectedTime} ha sido confirmada
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-muted/50 p-4 rounded-lg space-y-2">
              <p className="text-sm text-muted-foreground">
                <strong className="text-foreground">Actividad:</strong> {currentActivity?.name}
              </p>
              <p className="text-sm text-muted-foreground">
                <strong className="text-foreground">Horario:</strong> {selectedTime}
              </p>
              <p className="text-sm text-muted-foreground">
                <strong className="text-foreground">Participantes:</strong> {participants.length}
              </p>
            </div>
            <p className="text-sm text-muted-foreground text-center">
              Recibirás un correo de confirmación con todos los detalles de tu reserva.
            </p>
            <Button onClick={resetForm} className="w-full">
              Realizar otra inscripción
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-accent/5 to-secondary/10 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-4">
            <Leaf className="w-8 h-8 text-primary" />
            <h1 className="text-4xl font-bold text-foreground">EcoHarmony Park</h1>
          </div>
          <p className="text-lg text-muted-foreground">Inscripción a Actividades</p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center gap-2">
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-colors ${
                    step >= s ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                  }`}
                >
                  {s}
                </div>
                {s < 3 && <div className={`w-12 h-1 mx-2 transition-colors ${step > s ? "bg-primary" : "bg-muted"}`} />}
              </div>
            ))}
          </div>
          <div className="flex justify-between mt-2 text-sm text-muted-foreground max-w-md mx-auto">
            <span>Actividad</span>
            <span>Horario</span>
            <span>Participantes</span>
          </div>
        </div>

        {/* Step 1: Select Activity */}
        {step === 1 && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Selecciona una Actividad</CardTitle>
                <CardDescription>Elige la actividad que deseas realizar durante tu visita</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  {activities.map((activity) => {
                    const hasAvailability = activity.availableSlots.some((s) => s.available > 0)
                    return (
                      <Card
                        key={activity.id}
                        className={`cursor-pointer transition-all hover:shadow-md ${
                          selectedActivity === activity.id ? "ring-2 ring-primary" : "hover:border-primary/50"
                        } ${!hasAvailability ? "opacity-60" : ""}`}
                        onClick={() => hasAvailability && handleActivitySelect(activity.id)}
                      >
                        <CardHeader>
                          <div className="flex items-start justify-between">
                            <CardTitle className="text-lg">{activity.name}</CardTitle>
                            {!hasAvailability && (
                              <Badge variant="destructive" className="text-xs">
                                Sin cupos
                              </Badge>
                            )}
                          </div>
                          <CardDescription className="text-sm">{activity.description}</CardDescription>
                        </CardHeader>
                        <CardContent>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              <span>1 hora</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Users className="w-4 h-4" />
                              <span>{activity.availableSlots.reduce((sum, s) => sum + s.available, 0)} cupos</span>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 2: Select Time and Participant Count */}
        {step === 2 && currentActivity && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{currentActivity.name}</CardTitle>
                    <CardDescription>{currentActivity.description}</CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => setStep(1)}>
                    Cambiar
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Time Selection */}
                <div className="space-y-3">
                  <Label className="text-base font-semibold">Selecciona el Horario</Label>
                  <RadioGroup value={selectedTime} onValueChange={handleTimeSelect}>
                    <div className="grid gap-3 md:grid-cols-2">
                      {currentActivity.availableSlots.map((slot) => (
                        <div key={slot.time} className="relative">
                          <RadioGroupItem
                            value={slot.time}
                            id={slot.time}
                            disabled={slot.available === 0}
                            className="peer sr-only"
                          />
                          <Label
                            htmlFor={slot.time}
                            className={`flex items-center justify-between p-4 rounded-lg border-2 cursor-pointer transition-all ${
                              slot.available === 0
                                ? "opacity-50 cursor-not-allowed bg-muted"
                                : "hover:border-primary/50 peer-data-[state=checked]:border-primary peer-data-[state=checked]:bg-primary/5"
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <Clock className="w-5 h-5 text-muted-foreground" />
                              <span className="font-semibold">{slot.time}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              {slot.available > 0 ? (
                                <>
                                  <Users className="w-4 h-4 text-muted-foreground" />
                                  <span className="text-sm text-muted-foreground">{slot.available} disponibles</span>
                                </>
                              ) : (
                                <Badge variant="destructive" className="text-xs">
                                  Completo
                                </Badge>
                              )}
                            </div>
                          </Label>
                        </div>
                      ))}
                    </div>
                  </RadioGroup>
                </div>

                <Separator />

                {/* Participant Count */}
                <div className="space-y-3">
                  <Label htmlFor="participant-count" className="text-base font-semibold">
                    Cantidad de Participantes
                  </Label>
                  {selectedSlot && (
                    <p className="text-sm text-muted-foreground">
                      Cupos disponibles para este horario: {selectedSlot.available}
                    </p>
                  )}
                  <Input
                    id="participant-count"
                    type="number"
                    min="1"
                    max={selectedSlot?.available || 1}
                    value={participantCount}
                    onChange={(e) => handleParticipantCountChange(e.target.value)}
                    className="max-w-xs"
                  />
                </div>

                <div className="flex justify-end">
                  <Button onClick={() => setStep(3)} disabled={!canProceedToStep3} size="lg">
                    Continuar
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Step 3: Participant Details and Terms */}
        {step === 3 && currentActivity && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Datos de los Participantes</CardTitle>
                    <CardDescription>Completa la información de cada persona que participará</CardDescription>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => setStep(2)}>
                    Volver
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {participants.map((participant, index) => (
                  <div key={index} className="space-y-4 p-4 border rounded-lg bg-card">
                    <h3 className="font-semibold text-lg">Participante {index + 1}</h3>
                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="space-y-2">
                        <Label htmlFor={`name-${index}`}>
                          Nombre Completo <span className="text-destructive">*</span>
                        </Label>
                        <Input
                          id={`name-${index}`}
                          value={participant.name}
                          onChange={(e) => updateParticipant(index, "name", e.target.value)}
                          placeholder="Juan Pérez"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`dni-${index}`}>
                          DNI <span className="text-destructive">*</span>
                        </Label>
                        <Input
                          id={`dni-${index}`}
                          value={participant.dni}
                          onChange={(e) => updateParticipant(index, "dni", e.target.value)}
                          placeholder="12345678"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor={`age-${index}`}>
                          Edad <span className="text-destructive">*</span>
                        </Label>
                        <Input
                          id={`age-${index}`}
                          type="number"
                          value={participant.age}
                          onChange={(e) => updateParticipant(index, "age", e.target.value)}
                          placeholder="25"
                        />
                      </div>
                      {currentActivity.requiresClothingSize && (
                        <div className="space-y-2">
                          <Label htmlFor={`size-${index}`}>
                            Talla de Vestimenta <span className="text-destructive">*</span>
                          </Label>
                          <Select
                            value={participant.clothingSize}
                            onValueChange={(value) => updateParticipant(index, "clothingSize", value)}
                          >
                            <SelectTrigger id={`size-${index}`}>
                              <SelectValue placeholder="Seleccionar talla" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="xs">XS</SelectItem>
                              <SelectItem value="s">S</SelectItem>
                              <SelectItem value="m">M</SelectItem>
                              <SelectItem value="l">L</SelectItem>
                              <SelectItem value="xl">XL</SelectItem>
                              <SelectItem value="xxl">XXL</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                <Separator />

                {/* Terms and Conditions */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">Términos y Condiciones</h3>
                  <div className="p-4 bg-muted/50 rounded-lg border">
                    <p className="text-sm text-foreground leading-relaxed">{currentActivity.terms}</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <Checkbox
                      id="terms"
                      checked={termsAccepted}
                      onCheckedChange={(checked) => setTermsAccepted(checked as boolean)}
                    />
                    <Label htmlFor="terms" className="text-sm font-normal leading-relaxed cursor-pointer">
                      Acepto los términos y condiciones específicos de la actividad{" "}
                      <span className="text-destructive">*</span>
                    </Label>
                  </div>
                </div>

                {!canSubmit() && (
                  <div className="flex items-start gap-2 p-3 bg-accent/10 border border-accent rounded-lg">
                    <AlertCircle className="w-5 h-5 text-accent shrink-0 mt-0.5" />
                    <p className="text-sm text-foreground">
                      Por favor completa todos los campos requeridos y acepta los términos y condiciones para continuar.
                    </p>
                  </div>
                )}

                <div className="flex justify-end">
                  <Button onClick={handleSubmit} disabled={!canSubmit()} size="lg" className="min-w-[200px]">
                    Confirmar Inscripción
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
